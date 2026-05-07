def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_move():
        if not resources:
            cx, cy = (gw - 1) // 2, (gh - 1) // 2
            best = (0, 0)
            bestv = -10**9
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                v = -cheb(nx, ny, cx, cy)
                if (nx, ny) != (sx, sy):
                    v += 0.01
                if v > bestv:
                    bestv, best = v, (dx, dy)
            return list(best)

        # Evaluate immediate move by resource desirability with opponent competition
        # Prefer resources we can reach first; otherwise choose those that minimize opponent advantage.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = 0
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if sd == 0:
                    v += 10000  # guaranteed pickup
                else:
                    # own closeness
                    v += 40 / (sd + 1)
                    # competition: reward if we are closer than opponent
                    diff = od - sd
                    if diff > 0:
                        v += 25 * diff
                    elif diff == 0:
                        v -= 3
                    else:
                        v -= 20 / (abs(diff) + 1)
            # Small obstacle-avoidance: discourage moving next to obstacles
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in obstacles:
                    v -= 0.8
            # Deterministic tie-break: prefer not staying still slightly
            if (dx, dy) != (0, 0):
                v += 0.001
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    return best_move()