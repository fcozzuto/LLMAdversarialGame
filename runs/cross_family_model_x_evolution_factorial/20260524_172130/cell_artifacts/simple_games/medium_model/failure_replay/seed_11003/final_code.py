def choose_move(observation):
    # Defensive, deterministic policy that works across observation types
    grid_w = observation.get("grid_width", 0)
    grid_h = observation.get("grid_height", 0)

    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])

    sx, sy = self_pos
    ox, oy = opp_pos

    # 1) Threat avoidance: move away from opponent if present
    dxo = sx - ox
    dyo = sy - oy
    if abs(dxo) + abs(dyo) > 0:
        if abs(dxo) >= abs(dyo):
            x = -1 if dxo > 0 else (1 if dxo < 0 else 0)
            y = 0
        else:
            x = 0
            y = -1 if dyo > 0 else (1 if dyo < 0 else 0)
        return [x, y]

    # 2) If no immediate threat, head toward a resource if available
    resources = observation.get("resources", [])
    if resources:
        rx, ry = resources[0].get("pos", [0, 0])
        dx = 1 if rx > sx else (-1 if rx < sx else 0)
        dy = 1 if ry > sy else (-1 if ry < sy else 0)
        return [dx, dy]

    # 3) Fallback deterministic exploration within bounds, avoiding opponent cell
    if grid_w and grid_h:
        # Try move right
        nx = (sx + 1) % grid_w
        ny = sy
        if (nx, ny) != (ox, oy):
            return [1, 0]
        # Try move left
        nx = (sx - 1) % grid_w
        if (nx, ny) != (ox, oy):
            return [-1, 0]
        # Try move up
        nx = sx
        ny = (sy + 1) % grid_h
        if (nx, ny) != (ox, oy):
            return [0, 1]
        # Try move down
        ny = (sy - 1) % grid_h
        if (nx, ny) != (ox, oy):
            return [0, -1]
        # If all blocked by opponent, stay
        return [0, 0]

    # 4) If no grid info, stay as safe default
    return [0, 0]
