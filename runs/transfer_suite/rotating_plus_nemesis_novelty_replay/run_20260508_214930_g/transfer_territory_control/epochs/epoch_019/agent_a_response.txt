def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def neigh_open(nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                mx, my = nx + dx, ny + dy
                if 0 <= mx < w and 0 <= my < h and (mx, my) not in obstacles:
                    c += 1
        return c

    best = [0, 0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        target = (nx, ny)
        sc = 0

        a_self = adj_count(nx, ny, self_t)
        a_opp = adj_count(nx, ny, opp_t)
        open_n = neigh_open(nx, ny)

        if target in self_t:
            sc += 8 + a_self
            sc += 0.1 * open_n
        elif target in opp_t:
            sc += 40 + 6 * a_opp + 3 * a_self
            sc -= 2 * adj_count(nx, ny, self_t) * 0  # keep deterministic no-op
        elif target in unclaimed:
            sc += 14 + 3 * a_self - 2 * a_opp
            sc += 0.1 * open_n
        else:
            sc += 6 + 2 * a_self - 2 * a_opp

        # Encourage expanding toward borders of opponent territory
        if a_opp > 0:
            sc += 5 * a_opp

        # Penalize stepping away if also not near opponent
        dist_to_opp = 0
        if opp_t:
            # cheap deterministic estimate: min manhattan to subset corners-ish
            cand = list(opp_t)
            step = max(1, len(cand) // 6)
            m = 10**9
            for i in range(0, len(cand), step):
                ox, oy = cand[i]
                d = abs(ox - nx) + abs(oy - ny)
                if d < m:
                    m = d
            dist_to_opp = m
        sc += -0.2 * dist_to_opp

        if sc > best_score:
            best_score = sc
            best = [dx, dy]
        elif sc == best_score:
            # tie-break: prefer non-stay, then lexicographic direction
            if best != [0, 0] and [dx, dy] == [0, 0]:
                continue
            if [dx, dy] != [0, 0]:
                best = [dx, dy] if best == [0, 0] else min(best, [dx, dy])

    return best