def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    targets = list(unclaimed) if unclaimed else (list(resources) if resources else [])
    # Pick a small subset deterministically
    if targets:
        # deterministic subset: sorted by (x,y)
        targets = sorted(targets)[:32]
        def dist_to_targets(x, y):
            best = 10**9
            for tx, ty in targets:
                d = manhattan(x, y, tx, ty)
                if d < best:
                    best = d
                    if best == 0:
                        break
            return best
    else:
        def dist_to_targets(x, y):
            return 0

    best_move = (0, 0)
    best_score = -10**18

    # Prefer advancing while avoiding obstacles; also bias toward flipping opponent territory.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**12 - (abs(dx) + abs(dy))  # discourage invalid, but deterministic
        else:
            if (nx, ny) in opp_terr:
                score = 2000
            elif (nx, ny) in unclaimed:
                score = 1400
            elif (nx, ny) in self_terr:
                score = 200
            elif (nx, ny) in resources:
                score = 900
            else:
                score = 0

            # Approach nearest target; also slightly prefer reducing distance to opponent territory boundary.
            score += max(0, 60 - dist_to_targets(nx, ny))
            if opp_terr:
                # nearest opponent territory cell (small subset)
                opp_list = sorted(opp_terr)[:24]
                bd = 10**9
                for ox, oy in opp_list:
                    d = manhattan(nx, ny, ox, oy)
                    if d < bd:
                        bd = d
                        if bd == 0:
                            break
                score += max(0, 35 - bd)
            # Tiny tie-breaker deterministic: prefer dx,dy closer to continuing direction from start corner
            score += (0.001 * (dx * (1 if sx == 0 else -1 if sx == w - 1 else 0) + dy * (1 if sy == 0 else -1 if sy == h - 1 else 0)))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]