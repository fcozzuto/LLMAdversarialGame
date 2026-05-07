def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)
    if t & 1:
        moves = moves[4:] + moves[:4]

    def dist2(a, b, x, y):
        dx = a - x
        dy = b - y
        return dx * dx + dy * dy

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        our_dists = []
        opp_dists = []
        for rx, ry in resources:
            our_dists.append(dist2(nx, ny, rx, ry))
            opp_dists.append(dist2(ox, oy, rx, ry))

        better = 0
        best_d = 10**18
        best_any = 10**18
        for i in range(len(resources)):
            od = our_dists[i]
            pd = opp_dists[i]
            if od < best_any:
                best_any = od
            if od <= pd:
                better += 1
                if od < best_d:
                    best_d = od
        chosen_d = best_d if best_d != 10**18 else best_any

        opp_close = min(opp_dists) if opp_dists else 0
        val = -chosen_d + 3.0 * better - 0.02 * opp_close
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move