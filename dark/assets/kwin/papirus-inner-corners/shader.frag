#version 140
in vec2 texcoord0;
in vec2 position0;
out vec4 fragColor;
#include "colormanagement.glsl"
#include "saturation.glsl"
uniform sampler2D sampler;
uniform vec4 modulation;
uniform vec2 expandedSize;
uniform vec2 frameOffset;
uniform vec4 clientRect;
uniform float innerRadius;
uniform float outlineWidth;
uniform vec4 outlineColor;
void main()
{
    bool inverted = dot(vec2(dFdx(texcoord0.y), dFdy(texcoord0.y)),
                        vec2(dFdx(position0.y), dFdy(position0.y))) > 0.0;
    vec2 p = vec2(texcoord0.x, inverted ? texcoord0.y : 1.0 - texcoord0.y) * expandedSize - frameOffset;
    vec2 q = p - clientRect.xy;
    vec4 color = texture(sampler, texcoord0);
    float r = min(innerRadius, 0.5 * min(clientRect.z, clientRect.w));
    if (q.y >= 0.0 && q.y < clientRect.w && q.x >= 0.0 && q.x < clientRect.z) {
        bool left = q.x < r;
        bool right = q.x > clientRect.z - r;
        bool top = q.y < r;
        bool bottom = q.y > clientRect.w - r;
        if ((left || right) && (top || bottom)) {
            vec2 center = vec2(left ? r : clientRect.z - r, top ? r : clientRect.w - r);
            float coverage = 1.0 - smoothstep(r - 0.65, r + 0.65, length(q - center));
            // Sample the existing side border, preserving active/inactive colors
            // and premultiplied alpha instead of revealing the desktop.
            vec2 borderPixel = vec2(left ? clientRect.x - 1.5 : clientRect.x + clientRect.z + 1.5,
                                    clientRect.y + center.y);
            vec2 borderTex = (borderPixel + frameOffset) / expandedSize;
            if (!inverted) borderTex.y = 1.0 - borderTex.y;
            color = mix(texture(sampler, borderTex), color, coverage);
        }
        if (outlineWidth > 0.0) {
            // A one-pixel inset stroke around the same rounded rectangle.
            vec2 halfSize = clientRect.zw * 0.5;
            vec2 d = abs(q - halfSize) - (halfSize - vec2(r));
            float distanceToEdge = length(max(d, vec2(0.0))) + min(max(d.x, d.y), 0.0) - r;
            float outerCoverage = 1.0 - smoothstep(-0.5, 0.5, distanceToEdge);
            float stroke = smoothstep(-outlineWidth - 0.5, -outlineWidth + 0.5, distanceToEdge) * outerCoverage;
            color = mix(color, outlineColor, stroke);
        }
    }
    color = sourceEncodingToNitsInDestinationColorspace(color);
    color = adjustSaturation(color) * modulation;
    fragColor = nitsToDestinationEncoding(color);
}
