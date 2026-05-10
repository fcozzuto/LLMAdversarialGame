def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    # Prefer unclaimed that are on/near opponent territory boundary (likely to flip/claim quickly)
    frontier_targets = []
    if opp_terr and unclaimed:
        for ux, uy in unclaimed:
            for nx, ny in neigh8(ux, uy):
                if (nx, ny) in opp_terr:
                    frontier_targets.append((ux, uy))
                    break

    targets = frontier_targets or list(unclaimed)
    if not targets:
        # No expansion targets: defend by staying on self territory and not colliding
        candidates = [(sx + dx, sy + dy, dx, dy) for dx, dy in moves]
        best = None
        for nx, ny, dx, dy in candidates:
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = (0.2 if (nx, ny) in self_terr else 0.0) - 0.01 * man(nx, ny, opp_pos[0], opp_pos[1])
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    # Choose best move via immediate cell value + attraction to best target
    # (Deterministic: pick nearest target for attraction term.)
    tx, ty = min(targets, key=lambda c: man(sx, sy, c[0], c[1]))

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        val = 0.0
        if cell in opp_terr:
            val += 6.0  # flipping opponent control directly on entry
        if cell in unclaimed:
            val += 3.5  # strong early expansion
        if cell in self_terr:
            val += 0.25  # slight preference to remain stable

        # Encourage movement toward selected target, but penalize drifting away from opponent when attacking
        dist_self = man(nx, ny, sx, sy)
        dist_to_t = man(nx, ny, tx, ty)
        dist_to_opp = man(nx, ny, opp_pos[0], opp_pos[1])
        val += -0.12 * dist_to_t
        val += (0.08 if cell in opp_terr else 0.0)
        val += -0.02 * dist_self
        val += -0.03 * dist_to_opp

        # Tiny tie-break: prefer staying still if values equal
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]