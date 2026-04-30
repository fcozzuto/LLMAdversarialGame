def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem)
    except:
        rem = len(resources)

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    targets = res if (rem > 0 and res) else []
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if targets:
            d_to_res = min(cheb(nx, ny, tx, ty) for tx, ty in targets)
            d_to_opp = cheb(nx, ny, ox, oy)
            # Prefer closer to resources; also keep some distance from opponent.
            val = -3 * d_to_res + d_to_opp
        else:
            d_to_opp = cheb(nx, ny, ox, oy)
            val = d_to_opp
        # Tie-break deterministically toward non-diagonal then toward (0,0)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]