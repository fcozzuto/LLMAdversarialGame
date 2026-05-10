def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2 and p[0] is not None and p[1] is not None)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2 and p[0] is not None and p[1] is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        if unclaimed:
            # maximize by minimizing distance to nearest unclaimed
            nearest = min(md(nx, ny, ux, uy) for ux, uy in unclaimed)
            score = -nearest
        else:
            score = -md(nx, ny, ox, oy)  # fallback: move toward opponent
        # tie-break: prefer moves that reduce distance to opponent and avoid staying when possible
        score = score * 1000 - md(nx, ny, ox, oy) * 3 - (dx == 0 and dy == 0)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    # last resort: deterministic safe in-bounds move (or stay if none)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy):
            return [dx, dy]
    return [0, 0]