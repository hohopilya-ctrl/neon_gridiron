shader_type spatial;

uniform vec3 grid_color : source_color = vec3(0.0, 0.8, 1.0);
uniform vec3 background_color : source_color = vec3(0.05, 0.05, 0.1);
uniform float grid_thickness : hint_range(0.01, 0.1) = 0.02;
uniform float grid_size : hint_range(0.1, 5.0) = 1.0;
uniform float pulse_speed : hint_range(0.1, 5.0) = 1.0;
uniform float pulse_intensity : hint_range(0.0, 1.0) = 0.2;
uniform vec2 ball_pos;

void fragment() {
    vec2 uv = UV * 100.0 / grid_size;
    vec2 grid = abs(fract(uv - 0.5) - 0.5) / fwidth(uv);
    float line = min(grid.x, grid.y);
    float grid_mask = 1.0 - smoothstep(0.0, grid_thickness * 50.0, line);
    
    // Pulse effect
    float pulse = sin(TIME * pulse_speed) * 0.5 + 0.5;
    vec3 animated_color = grid_color * (1.0 + pulse * pulse_intensity);
    
    // Distance from ball glow
    float dist_to_ball = distance(UV * vec2(60.0, 40.0), ball_pos);
    float ball_glow = exp(-dist_to_ball * 0.2) * 2.0;
    
    vec3 final_color = mix(background_color, animated_color + ball_glow * grid_color, grid_mask);
    
    ALBEDO = final_color;
    EMISSION = animated_color * grid_mask * 0.5 + ball_glow * grid_color * grid_mask;
}
