def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Deny mode: if opponent is closer to some resource, contest the most dangerous one.
    my_vs_opp = []
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        my_vs_opp.append((sd, od, rx, ry))
    contested = [t for t in my_vs_opp if t[1] < t[0] and t[0] <= 3]
    if contested:
        # Most dangerous: smallest opponent distance, tie-break toward closer self.
        sd, od, tx, ty = min(contested, key=lambda t: (t[1], t[0], t[2], t[3]))
    else:
        # Opportunity mode: maximize lead over opponent.
        sd, od, tx, ty = max(my_vs_opp, key=lambda t: (t[1] - t[0], -t[0], -t[2], -t[3]))

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = king_dist(nx, ny, tx, ty)
        opp_d = king_dist(ox, oy, tx, ty)

        # Approximate opponent greedy step: reduce their distance by 1 if they can.
        opp_next = opp_d - 1
        if opp_next < 0:
            opp_next = 0

        val = (opp_next - my_d) * 10 - my_d
        if val > best[1]:
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]