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
    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        # Secondary heuristic: keep away from walls (for evader) / move toward opponent-aligned axis (for pursuer)
        wall_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        align = -abs(ddx) - abs(ddy)

        if is_evader:
            # Maximize distance; slight preference to stay away from walls to avoid corner traps
            score = (d2, wall_dist, -abs(nx - (w - 1) if ox >= w // 2 else 0) + -abs(ny - (h - 1) if oy >= h // 2 else 0), -dx, -dy)
            choose_better = best_score is None or score > best_score
        else:
            # Minimize distance; if tied, move that improves alignment (heads toward opponent), then avoid walls if possible
            score = (-d2, align, wall_dist, -dx, -dy)
            choose_better = best_score is None or score > best_score

        if choose_better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]