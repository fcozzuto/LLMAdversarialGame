def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    # Choose a target: first prefer resources we can reach no later than opponent.
    # If none, choose a "race" that most reduces opponent advantage.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man((sx, sy), (rx, ry))
        do = man((ox, oy), (rx, ry))
        can = 1 if ds <= do else 0
        # tie-break: prioritize earlier arrival; then farther to opponent (less likely they take it first)
        key = (can, -(ds), do - ds, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Greedy step toward target with obstacle-aware tie-breaking.
    # Also slightly bias toward moves that increase our lead over opponent.
    best_step = None
    for dx, dy, nx, ny in legal:
        ns = man((nx, ny), (tx, ty))
        ds_now = man((sx, sy), (tx, ty))
        do = man((ox, oy), (tx, ty))
        lead_now = do - ds_now
        lead_next = do - ns
        # Prefer reducing remaining distance; if equal, prefer improving lead.
        step_key = (-(ns), lead_next - lead_now, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_step is None or step_key > best_step[0]:
            best_step = (step_key, dx, dy)
    return [best_step[1], best_step[2]]