def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Defensive: move to maximize distance from opponent while staying valid.
        best_mv = (0, 0)
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]

    # Target resource where we are relatively closer than opponent.
    best_res = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = 2 * ds - do  # lower is better: we want small ds and large do
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Move evaluation: go toward target; avoid squares that let opponent become much closer next.
    best_mv = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist_to_t = cheb(nx, ny, tx, ty)
        opp_next = cheb(ox, oy, tx, ty)
        # Opponent effect: discourage moves that reduce our lead too much.
        lead_now = (cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty))
        lead_next = (dist_to_t - opp_next)
        lead_pen = (lead_next - lead_now)
        score = -dist_to_t * 10 + (cheb(nx, ny, ox, oy)) - 5 * lead_pen
        # Prefer staying closer to target directionally to break ties deterministically.
        score += - (abs((nx - tx)) + abs((ny - ty))) * 0.001
        if score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]