def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_response_distance(our_pos):
        best = -1
        best_moves = []
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny):
                nx, ny = ox, oy
            d = dist((nx, ny), our_pos)
            if d > best:
                best = d
                best_moves = [(dx, dy)]
            elif d == best:
                best_moves.append((dx, dy))
        # deterministic tie-break: smallest dx, then dy
        best_moves.sort()
        return best

    # if already on top, stay
    if sx == ox and sy == oy:
        return [0, 0]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if nx == ox and ny == oy:
            return [dx, dy]
        brd = best_response_distance((nx, ny))
        # primary: minimize distance after opponent best response; secondary: minimize immediate distance; tertiary: prefer staying still less
        immediate = dist((nx, ny), (ox, oy))
        score = (brd, immediate, abs(dx) + abs(dy))
        candidates.append((score, [dx, dy]))

    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]