def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "")
    is_evader = "evader" in role.lower()

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        # Secondary: bias against walls for evader, bias toward staying in center for both but stronger for evader.
        wd = wall_dist(nx, ny)
        center_bias = wd - (w + h) * 0.25  # constant shift; fine for ordering

        # Tertiary: prefer moving in the direction that increases/decreases max coordinate gap deterministically.
        gapx = abs(nx - ox)
        gapy = abs(ny - oy)
        maxgap = gapx if gapx >= gapy else gapy
        minwall = wd

        if is_evader:
            # Maximize distance, then maximize wall distance (avoid being cornered), then maximize max coordinate gap.
            score = (d2, minwall, maxgap, center_bias, -abs(dx) - abs(dy))
            if best is None or score > best:
                best = score
                best_move = (dx, dy)
        else:
            # Pursuer: minimize distance, then maximize wall distance (avoid getting stuck), then minimize max coordinate gap.
            score = (-d2, -abs(nx - ox) - abs(ny - oy), -minwall, -maxgap, -(abs(dx) + abs(dy)))
            if best is None or score > best:
                best = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]