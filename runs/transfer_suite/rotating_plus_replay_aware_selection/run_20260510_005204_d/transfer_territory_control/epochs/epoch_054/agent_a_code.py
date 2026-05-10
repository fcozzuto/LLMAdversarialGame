def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    oppx, oppy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

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

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def is_border(x, y, terrset):
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) not in terrset:
                return True
        return False

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        center_dist = abs(nx - cx) + abs(ny - cy)
        opp_dist = abs(nx - oppx) + abs(ny - oppy)

        in_unclaimed = (nx, ny) in unclaimed
        in_opp = (nx, ny) in opp_terr
        on_self = (nx, ny) in self_terr

        frontier = 1 if is_border(nx, ny, self_terr) else 0
        au = adj_unclaimed_count(nx, ny)

        score = 0
        score += 60 * au
        score += 18 * frontier
        score += 10 * (-center_dist)
        score += 6 * (-opp_dist)

        if in_unclaimed:
            score += 120
            score += 10 * frontier
        if in_opp:
            # territory flipping enabled on entry; only take if it also helps expansion
            score += 30 + 40 * min(2, au)
            score -= 35 * (1 if is_border(nx, ny, opp_terr) else 0)
        if on_self:
            score -= 3  # don't linger unless it positions well

        # Encourage steady progress after a long time remaining: favor unclaimed
        tr = int(observation.get("turns_remaining", 0))
        if tr < 20 and not in_unclaimed and not in_opp:
            score -= 25

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]