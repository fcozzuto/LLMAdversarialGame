def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    def manh(x, y, u, v):
        return abs(x - u) + abs(y - v)

    self_role = str(observation.get("self_role", ""))
    pursuer_like = ("purs" in self_role.lower()) or ("catch" in self_role.lower()) or ("hunter" in self_role.lower())
    evader_like = ("evad" in self_role.lower()) or ("escape" in self_role.lower()) or ("runner" in self_role.lower())
    if not (pursuer_like or evader_like):
        # Fallback: if role unclear, assume we are pursuer (common in pursuit-evasion setups)
        pursuer_like = True

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    opp_far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
    my_far_corner = max(corners, key=lambda c: manh(sx, sy, c[0], c[1]))
    # Deterministic move ordering
    moves = sorted(moves, key=lambda d: (d[0], d[1]))

    best = (None, -10**18 if not pursuer_like else 10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        ncnt = neighbors(nx, ny)
        if pursuer_like and not evader_like:
            # Minimize distance to opponent; prefer more mobility.
            val = (-d * 1000) + (ncnt * 10)
            # Tie-break toward farthest-from-opponent corner for pursuer pressure (often blocks evader).
            val += -manh(nx, ny, opp_far_corner[0], opp_far_corner[1])
            if val > best[1]:
                best = ([dx, dy], val)
        else:
            # Evader: maximize distance; prefer moving toward my farthest corner and higher mobility.
            val = (d * 1000) + (ncnt * 10)
            val += manh(nx, ny, my_far_corner[0], my_far_corner[1])
            if val > best[1]:
                best = ([dx, dy], val)

    if best[0] is None:
        return [0, 0]
    return best[0]