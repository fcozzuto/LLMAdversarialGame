def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def step_options(px, py):
        opts = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                opts.append((nx, ny))
        if not opts:
            opts = [(px, py)]
        return opts

    opp_steps = step_options(ox, oy)
    self_steps = step_options(x, y)

    best_move = (None, (-10**9, None))
    # Pick a target that balances (our ability to reach first) and (how much we can worsen opponent next turn)
    for tx, ty in resources:
        ds = man(x, y, tx, ty)
        do = man(ox, oy, tx, ty)
        base = (1 if ds <= do else 0, do - ds, -ds, -tx, -ty)
        # For determinism and to react differently from pure chasing, also bias toward targets where opponent is "close enough to steal"
        steal_pressure = 1 if do <= ds + 2 else 0
        base = (base, steal_pressure)
        # Evaluate best immediate move against this target with simple opponent-response simulation
        for nx, ny in self_steps:
            nds = man(nx, ny, tx, ty)
            # Assume opponent on this target moves to minimize distance to it
            nod = min(man(px, py, tx, ty) for px, py in opp_steps)
            # Our desirability: winning now, then maximizing opponent disadvantage, then shorter distance to finish
            win = 1 if nds <= nod else 0
            val = (win, (nod - nds), -nds, -tx, -ty)
            if best_move[0] is None or val > best_move[1][0] or (val == best_move[1][0] and (nx - x, ny - y) < best_move[0]):
                best_move = ((nx - x, ny - y), (val, base))

    dx, dy = best_move[0]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]