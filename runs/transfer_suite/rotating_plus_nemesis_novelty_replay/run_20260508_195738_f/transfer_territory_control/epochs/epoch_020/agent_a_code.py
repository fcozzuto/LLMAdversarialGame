def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_list = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obs_list)
    unclaimed = observation.get("unclaimed_cells", []) or []
    un = set((p[0], p[1]) for p in unclaimed)
    opp_t = observation.get("opponent_territory", []) or []
    opp = set((p[0], p[1]) for p in opp_t)
    self_t = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def mindist_to_set(px, py, s):
        md = 10**9
        for ax, ay in s:
            d = abs(ax - px) + abs(ay - py)
            if d < md:
                md = d
        return md

    opp_pos = observation.get("opponent_position", [7, 7]) or [7, 7]
    ox, oy = opp_pos[0], opp_pos[1]
    has_un = len(un) > 0
    has_opp = len(opp) > 0

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in opp:
            score += 6.0
        elif (nx, ny) in un:
            score += 3.0
        elif (nx, ny) in self_t:
            score += 0.25
        else:
            score += 0.6

        if has_un:
            d = abs(nx - x) + abs(ny - y)
            nu = mindist_to_set(nx, ny, un)
            score += max(0.0, 8.0 - nu) * 0.45
            score += max(0.0, 2.0 - d) * 0.05

        if has_opp:
            no = mindist_to_set(nx, ny, opp)
            score += max(0.0, 6.0 - no) * 0.22

        score += max(0.0, 10 - (abs(ox - nx) + abs(oy - ny))) * 0.08

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]