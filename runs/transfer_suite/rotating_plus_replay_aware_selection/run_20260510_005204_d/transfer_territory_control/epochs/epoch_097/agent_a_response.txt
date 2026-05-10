def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    bestm = (0, 0)
    bestscore = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_opp(x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in oppT:
                return True
        return False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**15
        else:
            # Immediate gain heuristic: prefer flipping/claiming, then move toward opponent.
            if (nx, ny) in oppT:
                base = 250.0
            elif (nx, ny) in unclaimed:
                base = 120.0
            elif (nx, ny) in selfT:
                base = 30.0
            else:
                base = 50.0

            adj = 90.0 if neigh_opp(nx, ny) else 0.0

            # Keep pressure: reduce distance to opponent while not drifting into our own static areas.
            man = abs(nx - ox) + abs(ny - oy)
            drift = abs(nx - sx) + abs(ny - sy)
            toward = -18.0 * man
            # Avoid getting stuck: slight penalty for staying too often when movement possible.
            stay_pen = -10.0 if (dx == 0 and dy == 0) else 0.0

            score = base + adj + toward - 0.5 * drift + stay_pen

        if score > bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]