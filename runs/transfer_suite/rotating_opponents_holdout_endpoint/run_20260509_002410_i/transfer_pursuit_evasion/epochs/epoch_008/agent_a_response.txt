def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("pursuit" in role) or role == "pursuer"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def center_bias(px, py):
        # higher is better for pursuer
        return -((px - cx) * (px - cx) + (py - cy) * (py - cy))

    def corner_bias(px, py):
        # higher is better for evader
        return max(abs(px - ex) + abs(py - ey) for ex, ey in corners)

    best = None
    best_score = None

    # Deterministic tie-break: prefer moves in a fixed order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        d = dist2(nx, ny, ox, oy)
        avoid_edge = min(nx, ny, (w - 1) - nx, (h - 1) - ny)

        if pursuer:
            # minimize distance; also prefer central squares; discourage hugging edges a bit.
            score = (-d, center_bias(nx, ny) + 0.2 * avoid_edge, 0)
        else:
            # maximize distance; also keep toward a far corner; discourage hugging edges (but not too much).
            score = (d, corner_bias(nx, ny) - 0.15 * (min(nx, ny, (w - 1) - nx, (h - 1) - ny)), 0)

        if best is None:
            best = (dx, dy)
            best_score = score
        else:
            if pursuer:
                if score[0] > best_score[0]:
                    best, best_score = (dx, dy), score
                elif score[0] == best_score[0] and score[1] > best_score[1]:
                    best, best_score = (dx, dy), score
            else:
                if score[0] > best_score[0]:
                    best, best_score = (dx, dy), score
                elif score[0] == best_score[0] and score[1] > best_score[1]:
                    best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]