def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))
    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))
    oppx, oppy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    my_front = set()
    for (x, y) in self_terr:
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and ((nx, ny) in unclaimed or (nx, ny) in opp_terr):
                my_front.add((x, y))
                break

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in unclaimed:
            s += 60
        if (x, y) in opp_terr:
            s += 50
        if (x, y) in self_terr:
            s -= 5
        # avoid getting too close to obstacles by penalizing obstacle-neighborhood
        if inb(x, y):
            for dx, dy in moves:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    s -= 2
        # frontier push: prefer landing adjacent to unclaimed/opp territory
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in unclaimed:
                    s += 10
                elif (nx, ny) in opp_terr:
                    s += 6
                elif (nx, ny) in self_terr:
                    s += 1
        # deterministic tie-breakers: steer away from opponent only when we can't expand
        d_opp = abs(x - oppx) + abs(y - oppy)
        s += max(0, 14 - d_opp) * (5 if len(unclaimed) > 0 else -1)
        # small bias toward forward expansion (diagonal-friendly)
        s += (x - sx) + (y - sy)
        return s

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) and not (0 <= nx < w and 0 <= ny < h):
            continue
        # allow staying even if current cell is valid; obstacle check prevents invalid destinations
        if inb(nx, ny) or (dx == 0 and dy == 0 and (sx, sy) not in obstacles):
            s = score_cell(nx, ny)
            if s > best[0] or (s == best[0] and (dx, dy) < (best[1], best[2])):
                best = (s, dx, dy)

    return [int(best[1]), int(best[2])]