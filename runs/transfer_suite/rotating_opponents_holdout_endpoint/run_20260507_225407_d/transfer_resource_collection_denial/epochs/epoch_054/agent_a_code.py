def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    best_t = None
    best_val = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not valid(tx, ty):
            continue
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        # Prefer resources where we're not behind; otherwise chase slightly closer ones.
        val = (sd - od, sd, tx, ty)
        if best_val is None or val < best_val:
            best_val = val
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # If we can grab directly, do so.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny) and nx == tx and ny == ty:
            return [dx, dy]

    # Greedy with obstacle avoidance and opponent-blocking deterrent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        oppd = dist(nx, ny, ox, oy)
        # Small bias to increase separation from opponent while moving to target.
        score = (nd, -oppd, abs(dx) + abs(dy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback: no valid adjacent cell (rare); stay.
    return [int(best_move[0]), int(best_move[1])]