def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))
    obs_set = set(obs)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_cost(x, y):
        if (x, y) in obs_set:
            return 10**7
        if not obs:
            return 0
        bestd = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < bestd:
                bestd = d
        if bestd == 0:
            return 10**7
        if bestd == 1:
            return 200
        if bestd == 2:
            return 60
        if bestd == 3:
            return 20
        return 0

    def corner_target():
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    target = corner_target()

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        dcur = abs(sx - ox) + abs(sy - oy)
        dnxt = abs(nx - ox) + abs(ny - oy)

        if is_evader:
            # prefer increasing distance and heading toward the farthest corner from pursuer
            score = (dnxt - dcur) * 1000 + (abs(target[0] - nx) + abs(target[1] - ny)) * 3
        else:
            # prefer decreasing distance; if we're close, also prefer safer approach around obstacles
            score = (-dnxt + dcur) * 1000 - (abs(target[0] - nx) + abs(target[1] - ny)) * 0.2

        score -= obs_cost(nx, ny)

        # tiny deterministic tie-break favoring staying still only if equal
        score += 0.001 if (dx, dy) == (0, 0) else 0

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]