def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        x, y = p
        x = int(x); y = int(y)
        if inb(x, y):
            obst.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        x, y = r
        x = int(x); y = int(y)
        if inb(x, y) and (x, y) not in obst:
            res.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    remaining = int(observation.get("remaining_resource_count", len(res)) or len(res))
    chase_weight = 3.0 if remaining <= 6 else 1.6
    block_weight = 1.8 if remaining <= 6 else 1.0

    best_move = legal[0]
    best_val = -10**18

    target_list = res if res else [(ox, oy)]
    target_list = sorted(target_list, key=lambda p: (cheb(ox, oy, p[0], p[1]), p[0], p[1]))

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Evaluate vs the single best target for us under this move
        local_best = -10**18
        for tx, ty in target_list[:4]:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Prefer being closer than opponent; when tied, prefer moving that keeps opponent farther after they respond imperfectly.
            rel_adv = (d_opp - d_self)
            val = chase_weight * rel_adv - cheb(nx, ny, sx, sy) * 0.05
            # Encourage approach to a target that opponent is currently relatively far from
            val += block_weight * (cheb(sx, sy, tx, ty) - d_self) * 0.35
            if val > local_best:
                local_best = val
        # Deterministic tie-break: prefer smaller dx, then dy, then lexicographic position
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)
        elif local_best == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]