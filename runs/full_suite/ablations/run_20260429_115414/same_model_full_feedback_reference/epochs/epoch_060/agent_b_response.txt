def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (W - 1) // 2, (H - 1) // 2

    # Pick a contested target: prefer resources where we're closer than opponent; if none, pick where opponent is closest.
    best_target = resources[0]
    best_tscore = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        tscore = (do - ds) * 100 - ds  # strong priority to being earlier
        # slight deterministic center preference to avoid dithering
        tscore += - (cheb(rx, ry, cx, cy))
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    tx, ty = best_target
    cur_dop = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_mscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        ds_cur = cheb(sx, sy, tx, ty)
        # Move score: minimize our distance to target; also try to increase our distance from opponent (deny race)
        mscore = -(ds_next * 10 + (ds_next > ds_cur) * 5)
        dop_next = cheb(nx, ny, ox, oy)
        mscore += (dop_next - cur_dop) * 2
        # If already adjacent to target, prefer stepping onto it
        if ds_next == 0:
            mscore += 100000
        if best_mscore is None or mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]