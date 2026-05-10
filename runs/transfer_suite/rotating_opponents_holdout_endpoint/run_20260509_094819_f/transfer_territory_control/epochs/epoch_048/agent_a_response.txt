def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(oppT)
    if opp_list:
        def mindist_to_opp(x, y):
            best = 10**9
            for ox, oy in opp_list:
                d = abs(ox - x) + abs(oy - y)
                if d < best:
                    best = d
                    if best == 0:
                        break
            return best
    else:
        # If opponent territory is empty, push toward unclaimed near your side to claim space.
        un_list = list(uncla) if uncla else []
        if un_list:
            def mindist_to_opp(x, y):
                best = 10**9
                for ux, uy in un_list:
                    d = abs(ux - x) + abs(uy - y)
                    if d < best:
                        best = d
                        if best == 0:
                            break
                return best
        else:
            def mindist_to_opp(x, y):
                return 0

    def adj_opp(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if inb(nx, ny) and (nx, ny) in oppT:
                    return 1
        return 0

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        s = 0.0
        if (x, y) in selfT:
            s += 2.0
        if (x, y) in uncla:
            s += 7.0
        if (x, y) in oppT:
            s += 15.0
        d = mindist_to_opp(x, y)
        s += 3.5 / (1.0 + d)
        # Make meaningful strategic change: prioritize stepping onto cells that create immediate frontier pressure.
        s += 5.0 * adj_opp(x, y)
        # Mild preference for advancing (toward increasing x+y) when no opponent pressure exists.
        if not oppT and (x + y) > (sx + sy):
            s += 0.6
        return s

    best = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best:
            best = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]