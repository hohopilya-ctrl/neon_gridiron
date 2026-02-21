shader_type spatial;

uniform vec3 grid_color : source_color = vec3(0.0, 0.5, 1.0);
uniform float grid_size = 2.0;
uniform float line_width = 0.05;
uniform float pulse_speed = 2.0;

void fragment() {
    vec2 uv = UV * vec2(60.0, 40.0) / grid_size;
    vec2 grid = abs(fract(uv - 0.5) - 0.5) / fwidth(uv);
    float line = min(grid.x, grid.y);
    float mask = 1.0 - smoothstep(0.0, line_width * 10.0, line);
    
    // Pulsing effect
    float pulse = (sin(TIME * pulse_speed) * 0.5 + 0.5) * 0.5 + 0.5;
    
    ALBEDO = vec3(0.02, 0.02, 0.04); # Background dark blue
    EMISSION = grid_color * mask * 2.0 * pulse;
}
