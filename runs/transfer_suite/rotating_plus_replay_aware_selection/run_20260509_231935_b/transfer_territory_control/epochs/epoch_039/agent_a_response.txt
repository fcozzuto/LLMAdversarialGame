def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    d0 = t % len(dirs)
    dirs = dirs[d0:] + dirs[:d0]

    opp_list = list(opp_terr)[:200]
    un_list = list(unclaimed)[:200]

    def mind_to(cells, x, y):
        if not cells:
            return 99
        best = 10**9
        for px, py in cells:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    d_un = mind_to(un_list, sx, sy)
    d_opp = mind_to(opp_list, sx, sy)

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def adj_count(cellset, x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in cellset:
                c += 1
        return c

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 8
        if (nx, ny) in opp_terr:
            score += 10
        if (nx, ny) in self_terr:
            score -= 1

        score += 0.5 * adj_count(unclaimed, nx, ny)
        score += 0.3 * adj_count(opp_terr, nx, ny)
        score -= 0.02 * (abs(nx - sx) + abs(ny - sy))

        # Drive toward unclaimed if available; otherwise toward opponent territory boundary
        if un_list:
            score += 2.0 * (d_un - mind_to(un_list, nx, ny))
        if opp_list:
            score += 0.8 * (d_opp - mind_to(opp_list, nx, ny))

        # Tie-break deterministically: prefer smaller dx, then smaller dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]