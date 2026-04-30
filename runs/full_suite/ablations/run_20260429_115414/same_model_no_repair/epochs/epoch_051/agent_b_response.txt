def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx <= 0 else -dx  # won’t be used

    def dist2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cand.append((nx, ny, dx, dy))
    if not cand:
        return [0, 0]

    # Target: choose resource that maximizes "advantage" (closer than opponent, tie-break by position)
    def score_adv(tx, ty):
        ds = max(abs(sx - tx), abs(sy - ty))
        do = max(abs(ox - tx), abs(oy - ty))
        # Prefer resources where we are closer; otherwise reduce pressure.
        return (do - ds) * 1000 - ds * 3 + (tx * 7 + ty)

    best_t = None
    best_s = -10**18
    for rx, ry in resources:
        s = score_adv(rx, ry)
        if s > best_s:
            best_s = s
            best_t = (rx, ry)
    tx, ty = best_t

    # Local choice: among legal moves, minimize distance to target while avoiding moving into opponent "pressure".
    best = None
    best_val = 10**18
    for nx, ny, dx, dy in cand:
        d_to_t = max(abs(nx - tx), abs(ny - ty))
        d_to_o = max(abs(nx - ox), abs(ny - oy))
        # If we step onto a square adjacent to opponent, slightly penalize to reduce direct contention.
        # Also penalize moves that increase distance to target.
        val = d_to_t * 10 + (20 - d_to_o) * 2
        # Secondary tie-break: prefer moves that also reduce distance to the best target if already equal.
        val += dist2(nx, ny, tx, ty) * 0.001
        if val < best_val or (val == best_val and (dx, dy) < (best[2], best[3]) if best else True):
            best_val = val
            best = (nx, ny, dx, dy)

    return [best[2], best[3]]