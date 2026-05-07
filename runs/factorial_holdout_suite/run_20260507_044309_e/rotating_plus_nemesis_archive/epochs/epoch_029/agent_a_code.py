def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def tieb_key(d):
        return (-(d[0] == 1), -(d[1] == 1), d[0], d[1])
    dirs.sort(key=tieb_key)

    best_r = None
    best_r_val = None
    for r in resources:
        md = cheb(my_pos, r)
        od = cheb(opp_pos, r)
        # Prefer resources that we can reach sooner (or opponent is farther), while still choosing a reasonable proximity.
        val = (od - md) * 100 - md
        if best_r is None or val > best_r_val or (val == best_r_val and r < best_r):
            best_r = r
            best_r_val = val

    tx, ty = best_r
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        md = cheb((nx, ny), best_r)
        # Greedily reduce my distance; keep an eye on denial by not moving closer to resources where opponent is likely to arrive first.
        denial = cheb(opp_pos, best_r) - md
        val = denial * 100 - md
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]