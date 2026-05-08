def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p is None or len(p) < 2:
                continue
            s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")
    resources = to_set("resources")

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    if resources:
        # Prefer capturing/approaching resources deterministically
        tx, ty = min(resources, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        # Define edge target candidates: unclaimed adjacent to opponent territory, else opponent territory itself
        edge_unclaimed = set()
        for ax, ay in oppT:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nx, ny = ax + dx, ay + dy
                if inside(nx, ny) and (nx, ny) in unclaimed:
                    edge_unclaimed.add((nx, ny))
        if edge_unclaimed:
            tx, ty = min(edge_unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        elif oppT:
            tx, ty = min(oppT, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        else:
            # Fallback: expand toward unclaimed anywhere
            if unclaimed:
                tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
            else:
                return [0, 0]

    # Score local moves to be aggressive at opponent edges
    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in oppT:
            score = 1000
        else:
            score = 0
            if (nx, ny) in unclaimed:
                # entering unclaimed next to opponent is valuable for edge claiming
                near_opp = False
                for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    ax, ay = nx + ddx, ny + ddy
                    if inside(ax, ay) and (ax, ay) in oppT:
                        near_opp = True
                        break
                score += 300 if near_opp else 50
            # Prefer moving closer to chosen target
            score += 30 - (abs(tx - nx) + abs(ty - ny))
            # Mildly discourage dithering
            score -= 2 if (nx, ny) in selfT else 0

        # Tie-break deterministically by dx,dy then position
        if (score, -dx, -dy, nx, ny) > best:
            best = (score, -dx, -dy, nx, ny)

    return [int(-best[1]), int(-best[2])]