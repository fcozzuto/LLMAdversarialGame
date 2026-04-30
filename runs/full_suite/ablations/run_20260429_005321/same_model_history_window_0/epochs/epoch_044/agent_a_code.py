def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy)

    if resources:
        tx, ty = min(resources, key=lambda p: dist(sx, sy, p[0], p[1]))
    else:
        tx, ty = (w - 1) / 2, (h - 1) / 2

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            sc = -10**9
        else:
            d_target = dist(nx, ny, tx, ty)
            d_opp = dist(nx, ny, ox, oy)
            d_opp_now = dist(sx, sy, ox, oy)
            sc = -d_target + 0.15 * d_opp + 0.08 * (d_opp - d_opp_now)
            # Mild preference to not oscillate toward the opponent when resources are gone
            if not resources:
                sc += 0.05 * (d_opp - d_opp_now)
        if best_score is None or sc > best_score:
            best_score = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]