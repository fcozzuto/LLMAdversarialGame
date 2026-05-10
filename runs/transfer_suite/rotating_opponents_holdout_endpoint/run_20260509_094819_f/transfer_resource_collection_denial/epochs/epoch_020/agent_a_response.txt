def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def neighbors(x, y):
        ds = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        # deterministic ordering already
        out = []
        for dx, dy in ds:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((dx, dy))
        return out

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                sd = man(sx, sy, rx, ry)
                od = man(ox, oy, rx, ry)
                # Prefer resources we can reach sooner; else minimize opponent advantage.
                adv = od - sd  # positive means we are closer
                # Also include a small bias away from opponent to reduce being denied near contested spots.
                deny_bias = (sd - od)
                target_score = adv * 10 - sd + (0.2 * (-deny_bias))
                valid_resources.append((target_score, adv, -sd, -od, rx, ry))
    if valid_resources:
        valid_resources.sort(reverse=True)
        _, adv, _, _, tx, ty = valid_resources[0]
        best_move = (0, 0)
        best_key = None
        for dx, dy in neighbors(sx, sy):
            nx, ny = sx + dx, sy + dy
            d_to = man(nx, ny, tx, ty)
            d_cur = man(sx, sy, tx, ty)
            # Prefer strictly better progress; otherwise best among equal progress.
            # Add small tie-break to keep moving directionally rather than oscillating.
            opp_d = man(nx, ny, ox, oy)
            prog = d_cur - d_to
            key = (1 if prog > 0 else 0, prog, -d_to, opp_d, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources visible: move to reduce distance to center while also not approach opponent too much.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_key = None
    for dx, dy in neighbors(sx, sy):
        nx, ny = sx + dx, sy + dy
        dcent = man(nx, ny, cx, cy)
        dopp = man(nx, ny, ox, oy)
        key = (-dcent, dcent, -dopp, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]