def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    # Decide between "secure" (we are closer) and "deny" (opponent is closer) to differ from prior opportunistic switching.
    secure = []
    deny = []
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        if myd < opd:
            secure.append((myd, opd, rx, ry))
        else:
            deny.append((opd, myd, rx, ry))
    if secure:
        _, _, tx, ty = min(secure)  # closest we can secure
    else:
        # if opponent is closer to everything, contest the most urgent one they are near (smallest opponent distance)
        _, _, tx, ty = min(deny)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        # Prefer moves that decrease distance; tie-breaker favors reducing opponent's advantage locally.
        my_next = d
        opp_next = man(nx, ny, tx, ty)  # local symmetry; still deterministic
        score = (d, my_next - opp_next, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]