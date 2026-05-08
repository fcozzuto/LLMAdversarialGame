def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_adv = -10**9
        best_ds = 10**9
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            adv = dO - dS
            if adv > best_adv or (adv == best_adv and (dS < best_ds or (dS == best_ds and (rx + ry) < (best[0] + best[1])))):
                best_adv = adv
                best_ds = dS
                best = (rx, ry)
        tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # If we can grab immediately (standing on a listed resource), prioritize strongly.
        on_resource = 1 if (nx, ny) in resources else 0
        val = 100000 * on_resource + (d_op - d_to) * 1000 - d_to
        # Mild tie-break: prefer moves that reduce both coordinates distance (deterministic).
        val += -abs(nx - tx) - abs(ny - ty) * 0.01
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves were blocked (rare), stay.
    return [int(best_move[0]), int(best_move[1])]