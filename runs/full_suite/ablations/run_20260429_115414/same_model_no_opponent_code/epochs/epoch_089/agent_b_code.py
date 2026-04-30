def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    resources.sort()

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in resources:
            score += 1000

        d_self = cheb(nx, ny, ox, oy)  # keep distance from opponent
        d_opp_to_self = cheb(ox, oy, nx, ny)

        # Prefer moves that approach the closest resource and (secondarily) slow opponent progress
        if resources:
            cs = 10**9
            co = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                if ds < cs:
                    cs = ds
                ds_o = cheb(ox, oy, rx, ry)
                if ds_o < co:
                    co = ds_o
            score += 60 * (cs == 0) + 30 * (-cs)  # closer is better
            score += 10 * (-max(0, co - cs))     # if we're closer than opponent, advantage
        else:
            # No visible resources: drift to center-ish while staying away from opponent
            score += -cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            score += -2 * d_self

        # Tactical: avoid moving into immediate "contact" range where opponent can grab first
        score += -8 * (d_opp_to_self <= 1)

        # Deterministic tie-break: prefer lexicographically smaller move deltas
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]