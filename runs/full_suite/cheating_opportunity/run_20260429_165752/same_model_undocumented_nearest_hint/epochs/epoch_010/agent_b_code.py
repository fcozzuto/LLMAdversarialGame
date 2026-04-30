def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (10**9, -10**9, (0, 0))
    has_res = bool(resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if has_res:
            # Prefer resources where we are at least as close as opponent; otherwise, just nearest.
            my_first = 10**9
            opp_first = 10**9
            for rx, ry in resources:
                dm = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                if dm <= do:
                    if dm < my_first:
                        my_first, opp_first = dm, do
            if my_first == 10**9:
                for rx, ry in resources:
                    dm = man(nx, ny, rx, ry)
                    do = man(ox, oy, rx, ry)
                    if dm < my_first:
                        my_first, opp_first = dm, do
            # Lower distance to target, lower opponent distance, and keep away from opponent.
            score1 = my_first
            score2 = opp_first
            score3 = man(nx, ny, ox, oy)
            key = (score1, score2, -score3)
        else:
            # No resources: move away from opponent deterministically.
            d2 = man(nx, ny, ox, oy)
            key = ( -d2, 0, 0 )
        if key < best[:3] if isinstance(key, tuple) else False:
            pass
        # Compare with fixed tuple ordering
        if key < best[0:3]:
            best = (key[0], key[2] if len(key) > 2 else 0, (dx, dy))
        else:
            # handle tuple lengths consistently without extra imports
            if has_res:
                # compare using computed tuple directly
                if key[0] < best[0] or (key[0] == best[0] and key[2] > best[1]):
                    best = (key[0], key[2], (dx, dy))
            else:
                if -key[0] > best[1]:
                    best = (key[0], -key[0], (dx, dy))

    dx, dy = best[2]
    if not inb(sx + dx, sy + dy):
        return [0, 0]
    return [int(dx), int(dy)]