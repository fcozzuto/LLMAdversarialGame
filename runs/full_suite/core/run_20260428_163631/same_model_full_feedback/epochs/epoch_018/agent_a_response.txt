def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    res = observation.get("resources", []) or []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, 7 if sy >= h // 2 else 0
        tx, ty = max(0, min(w - 1, tx)), max(0, min(h - 1, ty))
    else:
        tx, ty = resources[0]

    # Try immediate pickup
    res_set = set(resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    best_move = (0, 0)
    best_score = -10**18

    if resources:
        # Deterministic tie-break: sort resources by coords
        resources = sorted(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        if not resources:
            # Default greedy toward target corner/center
            d = cheb(nx, ny, tx, ty)
            score = -d
        else:
            score = -10**18
            our_pos_d_self = cheb(nx, ny, ox, oy)
            # Higher advantage means we arrive earlier than opponent to that resource
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # If we can arrive before opponent, strongly prefer; otherwise avoid races.
                arrive_first_bonus = (opp_d - our_d) * 10
                # Small preference for closer resources once races are similar.
                closeness = -our_d
                # Mildly reduce getting too close to opponent (to avoid contested path mirroring).
                spread = - (our_pos_d_self - 1)
                cand = arrive_first_bonus + closeness + 0.2 * spread
                if cand > score:
                    score = cand
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: smaller dx, then smaller dy
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    if safe(sx + dx, sy + dy):
        return [int(dx), int(dy)]
    return [0, 0]