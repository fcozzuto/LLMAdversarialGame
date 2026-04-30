def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles
    cheb = lambda ax, ay, bx, by: (abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by))

    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def sorted_resources():
        return sorted(resources, key=lambda p: (p[0], p[1]))

    # Determine strategic mode: chase advantage vs. contest opponent-most-likely resource
    if resources:
        rr = sorted_resources()
        best_gap = -10**9
        best_opp_min = 10**9
        for rx, ry in rr:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap = opp_d - our_d
            if gap > best_gap:
                best_gap = gap
            if opp_d < best_opp_min:
                best_opp_min = opp_d
        mode_contest = best_gap < 0  # we are behind to all/most resources
    else:
        mode_contest = False

    candidates = []
    if not resources:
        # No resources visible: move toward center while avoiding obstacles and staying away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -0.12 * cheb(nx, ny, ox, oy) - 0.25 * near_obs(nx, ny) - 0.01 * (abs(nx - cx) + abs(ny - cy))
            candidates.append((v, dx, dy))
        candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
        return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]

    rr = sorted_resources()
    # Evaluate each move by best target resource under the selected mode
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        our_d0 = cheb(nx, ny, ox, oy)
        bestv = -