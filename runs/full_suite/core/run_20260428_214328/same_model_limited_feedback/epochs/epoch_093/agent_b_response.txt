def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        resources = [(sx, sy)]
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    # Choose target resource with deterministic score balancing self progress and opponent threat.
    best = None
    bestv = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        v = sd - 0.6 * od
        if bestv is None or v < bestv or (v == bestv and (rx, ry) < best):
            bestv = v
            best = (rx, ry)
    tx, ty = best
    # If we're already on target, stay.
    if sx == tx and sy == ty:
        return [0, 0]
    # Evaluate next moves: avoid obstacles/out of bounds, go toward target; mild separation from opponent.
    def move_value(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if not inb(nx, ny):
            return -10**9
        dist_t = abs(tx - nx) + abs(ty - ny)
        dist_o = abs(ox - nx) + abs(oy - ny)
        # Prefer not getting too close to opponent (possible contest), but still allow approach.
        sep_pen = 0
        if dist_o <= 1:
            sep_pen = 3
        # Small tie-break toward reducing opponent's distance to their target (passive interference).
        # Estimate their progress using same target (conservative, deterministic).
        od_now = abs(tx - ox) + abs(ty - oy)
        od_next = abs(tx - ox) + abs(ty - oy)  # opponent doesn't move here; keep simple.
        return -dist_t - sep_pen + 0.01 * (dist_o) - 0.001 * od_now
    best_delta = [0, 0]
    best_mv = None
    # Tie-breaking deterministic: lexicographic on delta after value.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        mv = move_value(nx, ny)
        if best_mv is None or mv > best_mv or (mv == best_mv and (dx, dy) < tuple(best_delta)):
            best_mv = mv
            best_delta = [dx, dy]
    return best_delta