def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)
    # If no resources, just move toward opponent's side to deny/pressure
    if not resources:
        tx, ty = (w - 1, h - 1) if sx <= w // 2 else (0, 0)
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            score = -(dist((nx, ny), (tx, ty))) - 0.1 * dist((nx, ny), (ox, oy))
            if best is None or score > best[0]: best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose resource that maximizes our advantage over opponent (minimax-ish)
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer larger (opponent far relative to us), then shorter self distance
        key = (od - sd, -sd, -abs((rx - sx) - (ry - sy)))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Move one step toward target with obstacle avoidance and light opponent consideration
    want = (tx - sx, ty - sy)
    # Direction bias toward target
    step_options = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: 
            continue
        # Primary: reduce manhattan to target; Secondary: avoid getting too close to opponent
        nxt_d = dist((nx, ny), (tx, ty))
        opp_d = dist((nx, ny), (ox, oy))
        # Small deterministic tie-break based on direction relative to want
        align = dx * (1 if want[0] > 0 else -1 if want[0] < 0 else 0) + dy * (1 if want[1] > 0 else -1 if want[1] < 0 else 0)
        score = -nxt_d + 0.02 * opp_d + 0.001 * align
        step_options.append((score, dx, dy))
    if not step_options:
        return [0, 0]
    step_options.sort(reverse=True)
    return [int(step_options[0][1]), int(step_options[0][2])]