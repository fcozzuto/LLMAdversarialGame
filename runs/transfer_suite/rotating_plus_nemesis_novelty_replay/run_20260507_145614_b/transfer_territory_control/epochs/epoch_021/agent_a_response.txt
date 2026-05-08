def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    # Heuristic: grab unclaimed, punish walking into opponent-controlled expansion pressure,
    # and opportunistically flip if we can step into opponent territory.
    opp_list = list(opp_t)
    un_list = list(unclaimed)
    best = (0, 0)
    bestv = -10**9

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        t = (nx, ny)

        v = 0
        if t in opp_t:
            v += 7
        elif t in unclaimed:
            v += 4
        elif t in self_t:
            v += 1
        else:
            v += 1

        if opp_list:
            m_d = 10**9
            for ot in opp_list:
                d = cheb((nx, ny), ot)
                if d < m_d:
                    m_d = d
            v += int((4 - min(4, m_d)) * 2)

        # Avoid getting too close if we can't flip now (reduce being swept)
        if opp_list and t not in opp_t:
            for ot in opp_list:
                if cheb((nx, ny), ot) == 1:
                    v -= 2
                    break

        # Prefer moves that are part of our current region or expand outward
        if t not in self_t:
            v += 1

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]