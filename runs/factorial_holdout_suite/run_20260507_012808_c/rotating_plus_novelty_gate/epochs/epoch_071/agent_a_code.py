def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        best_key = None
        for x, y in resources:
            d_me = man(sx, sy, x, y)
            d_op = man(ox, oy, x, y)
            # Race only when we have a real advantage; otherwise still push nearest.
            key = (d_op - d_me, -d_me)
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    # If diagonal step lands on obstacle, try axis move deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        if (sx + dx, sy) not in obstacles:
            dy = 0
        elif (sx, sy + dy) not in obstacles:
            dx = 0
        else:
            dx, dy = 0, 0
    return [int(dx), int(dy)]