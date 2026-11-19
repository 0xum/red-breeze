// SPDX-License-Identifier: GPL-3.0-only
#include <effect/offscreeneffect.h>
#include <effect/effecthandler.h>
#include <effect/effectwindow.h>
#include <core/output.h>
#include <core/pixelgrid.h>
#include <opengl/glutils.h>
#include <window.h>
#include <QVector4D>
#include <QColor>
#include <KSharedConfig>
#include <KConfigGroup>
#include <KDecoration3/Decoration>
#include <memory>

class InnerCorners : public KWin::OffscreenEffect
{
    Q_OBJECT
public:
    InnerCorners()
    {
        shader = KWin::ShaderManager::instance()->generateShaderFromFile(
            KWin::ShaderTrait::MapTexture | KWin::ShaderTrait::RoundedCorners,
            QString(), QStringLiteral(":/papirus-inner-corners-outline-v2/shader.frag"));
        reconfigure(ReconfigureAll);
        qInfo() << "Papirus internal corners: 8 px corners, 1 px outline, all decorated apps, blur preserved";
        KWin::effects->addRepaintFull();
    }
    ~InnerCorners() override { KWin::effects->addRepaintFull(); }
    bool isActive() const override { return bool(shader); }
    int requestedEffectChainPosition() const override { return 99; }
    static bool supported() { return KWin::effects->isOpenGLCompositing(); }
    void reconfigure(ReconfigureFlags) override
    {
        const auto config = KSharedConfig::openConfig(QStringLiteral("kwinrc"));
        config->reparseConfiguration();
        const KConfigGroup group(config, QStringLiteral("org.kde.kdecoration2"));
        const QString theme = group.readEntry("theme", QString());
        themeEnabled = group.readEntry("library", QString()) == QStringLiteral("org.kde.kwin.aurorae.v2")
            && (theme == QStringLiteral("__aurorae__svg__Moe") || theme == QStringLiteral("__aurorae__svg__MoeDark"));
        const auto globals = KSharedConfig::openConfig(QStringLiteral("kdeglobals"));
        globals->reparseConfiguration();
        const bool light = theme == QStringLiteral("__aurorae__svg__Moe");
        const KConfigGroup colors(globals, QStringLiteral("Colors:Window"));
        const QColor background = colors.readEntry("BackgroundNormal", light ? QColor(239, 240, 241) : QColor(32, 35, 38));
        const QColor foreground = colors.readEntry("ForegroundNormal", light ? QColor(35, 38, 41) : QColor(252, 252, 252));
        const double contrast = qBound(0.0, KConfigGroup(globals, QStringLiteral("KDE")).readEntry("frameContrast", 0.2), 1.0);
        // Match Breeze's separatorColor: mix Window and WindowText at frameContrast.
        outlineColor = QColor::fromRgbF(background.redF() * (1.0 - contrast) + foreground.redF() * contrast,
                                       background.greenF() * (1.0 - contrast) + foreground.greenF() * contrast,
                                       background.blueF() * (1.0 - contrast) + foreground.blueF() * contrast);
        KWin::effects->addRepaintFull();
    }
    bool applies(KWin::EffectWindow *w) const
    {
        return shader && themeEnabled && (w->isNormalWindow() || w->isDialog())
            && w->hasDecoration() && !w->isFullScreen() && w->window()
            && w->window()->maximizeMode() == KWin::MaximizeRestore
            && QString::fromLatin1(w->decoration()->metaObject()->className()).contains(QStringLiteral("Aurorae"));
    }
    bool drawWindow(const KWin::RenderTarget &target, const KWin::RenderViewport &viewport,
                    KWin::EffectWindow *w, int mask, const KWin::Region &region,
                    KWin::WindowPaintData &data) override
    {
        if (!applies(w)) {
            unredirect(w);
            return OffscreenEffect::drawWindow(target, viewport, w, mask, region, data);
        }
        const double scale = w->screen()->scale();
        const auto frame = KWin::snapToPixels(w->frameGeometry(), scale) * scale;
        const auto expanded = KWin::snapToPixels(w->expandedGeometry(), scale) * scale;
        const auto client = KWin::snapToPixels(w->clientGeometry(), scale) * scale;
        redirect(w);
        setShader(w, shader.get());
        KWin::ShaderManager::instance()->pushShader(shader.get());
        shader->setUniform("expandedSize", QVector2D(expanded.width(), expanded.height()));
        shader->setUniform("frameOffset", QVector2D(frame.topLeft() - expanded.topLeft()));
        shader->setUniform("clientRect", QVector4D(client.x() - frame.x(), client.y() - frame.y(), client.width(), client.height()));
        shader->setUniform("innerRadius", float(8.0 * scale));
        shader->setUniform("outlineWidth", float(scale));
        shader->setUniform("outlineColor", outlineColor);
        const bool result = OffscreenEffect::drawWindow(target, viewport, w, mask, region, data);
        KWin::ShaderManager::instance()->popShader();
        return result;
    }
private:
    bool themeEnabled = false;
    QColor outlineColor;
    std::unique_ptr<KWin::GLShader> shader;
};
KWIN_EFFECT_FACTORY_SUPPORTED(InnerCorners, "metadata.json", return InnerCorners::supported();)
#include "effect.moc"
