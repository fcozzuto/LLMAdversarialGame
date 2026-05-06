def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (None, None, -10**9)  # (dx,dy,score)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        best_gain = -10**9
        best_our_d = 10**9
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            gain = opp_d - our_d
            if gain > best_gain or (gain == best_gain and our_d < best_our_d) or (gain == best_gain and our_d == best_our_d and (rx, ry) < resources[0]):
                best_gain = gain
                best_our_d = our_d

        # Prefer making (and staying) the opponent disadvantaged; tie-break toward nearer resource.
        score = best_gain * 100 - best_our_d
        if score > best[2]:
            best = (dx, dy, score)

    if best[0] is None:
        return [0, 0]
    return [best[0], best[1]]