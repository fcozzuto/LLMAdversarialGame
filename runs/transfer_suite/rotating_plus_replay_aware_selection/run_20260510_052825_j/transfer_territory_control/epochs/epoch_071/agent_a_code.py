def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = set((p[0], p[1]) for p in unclaimed if p is not None and len(p) >= 2)

    selfT = observation.get("self_territory") or []
    selfT = set((p[0], p[1]) for p in selfT if p is not None and len(p) >= 2)

    oppT = observation.get("opponent_territory") or []
    oppT = set((p[0], p[1]) for p in oppT if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    un_list = sorted(unclaimed)
    opp_list = sorted(oppT)

    if not un_list and not opp_list:
        return [0, 0]

    INF = 10**9

    def nearest_dist(nx, ny, cells):
        if not cells:
            return INF
        best = INF
        for cx, cy in cells:
            d = abs(cx - nx) + abs(cy - ny)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in unclaimed:
            base = 22
        elif (nx, ny) in oppT:
            base = 14
        elif (nx, ny) in selfT:
            base = 7
        else:
            base = 1

        d_un = nearest_dist(nx, ny, un_list)
        d_opp = nearest_dist(nx, ny, opp_list)

        val = base
        if un_list:
            val += -0.6 * d_un
        if opp_list:
            val += -0.25 * d_opp
        if (nx, ny) in oppT:
            val += 0.15

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]