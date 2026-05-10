def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    obstacles = []
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.append((x, y))

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def obst_pen(nx, ny):
        if not obstacles:
            return 0.0
        best = 10**9
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        if best == 0:
            return 1e6
        if best == 1:
            return 30.0
        if best == 2:
            return 10.0
        return float(best) * 0.25

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -1e18 if pursuer else 1e18

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        d1 = abs(nx - ox) + abs(ny - oy)
        dch = max(abs(nx - ox), abs(ny - oy))
        cap = 1e9 if (d1 == 0 and observation.get("capture_radius", 0) == 0) else 0.0
        move_cost = 0.05 * (dx != 0 or dy != 0)
        op_corner_push = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        score = 0.0
        score += (cap + (1.5 / (d1 + 1.0)) + (1.0 / (dch + 1.0))) if pursuer else 0.0
        if pursuer:
            val = score - 0.9 * d1 - 0.6 * dch - obst_pen(nx, ny) - move_cost + (0.3 if op_corner_push else 0.0)
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best_val, best = val, (dx, dy)
        else:
            # Evader: run away from pursuer; also avoid obstacles
            val = (0.9 * d1 + 0.6 * dch) - obst_pen(nx, ny) - move_cost + (0.2 if op_corner_push else 0.0)
            if best is None or val < best_val or (val == best_val and (dx, dy) < best):
                best_val, best = val, (dx, dy)

    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]