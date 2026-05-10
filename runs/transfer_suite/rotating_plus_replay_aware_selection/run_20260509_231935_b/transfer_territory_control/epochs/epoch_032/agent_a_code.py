def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = map(int, observation["opponent_position"])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
        target_type = 0  # toward unclaimed
    elif opp_terr:
        px, py = min(opp_terr, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
        tx, ty = px, py
        target_type = 1  # attack
    else:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    k = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[k:] + dirs[:k]

    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            v = -10**12
        else:
            v = 0
            if (nx, ny) in opp_terr:
                v += 2000 - md(nx, ny, ox, oy)  # flipping opportunity
            elif (nx, ny) in unclaimed:
                v += 600 - md(nx, ny, tx, ty)  # expansion
            elif (nx, ny) in self_terr:
                v -= 5
            else:
                v += 20 - md(nx, ny, tx, ty)  # neutral space adjacent

            v += 3 * (md(sx, sy, tx, ty) - md(nx, ny, tx, ty))  # move closer to target
            v -= 2 * md(nx, ny, ox, oy) if target_type == 1 else 0  # when attacking, avoid running away

            if (nx, ny) == (ox, oy):
                v -= 50  # don't step directly onto opponent position if possible

        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]