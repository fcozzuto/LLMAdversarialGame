def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [int(dx), int(dy)]

    me = (sx, sy)
    opp = (ox, oy)

    # Pick one opponent target and one self target deterministically.
    opp_target = min(resources, key=lambda r: (man(opp, r), r[0], r[1]))

    # If we can get a resource quickly, prioritize it; otherwise, go for closest.
    self_target = min(resources, key=lambda r: ((man(me, r) - 0.15 * man(opp, r)), r[0], r[1]))

    best_move = [0, 0]
    best_val = -10**18

    # Evaluate next move impact on both agents.
    k_block = 0.9  # how much we care about denying opponent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine will keep us, but make deterministic evaluation
        nme = (nx, ny)

        # Self progress: decrease distance to our target.
        d0 = man(me, self_target)
        d1 = man(nme, self_target)

        # Opportunistic capture bonus if landing on any resource (deterministic).
        cap_bonus = 0
        if (nx, ny) in resources:
            cap_bonus = 30

        # Deny opponent: increase their distance to their target, or reduce their progress.
        od0 = man(opp, opp_target)
        od1 = man(opp, opp_target)  # opponent doesn't move in our control; use positional alignment heuristic instead
        # Alignment block: moving toward a line between opponent and target to "interfere" with sweep behavior.
        # Use sign-move toward the target and compare if we get closer to blocking cell near the line.
        tx, ty = opp_target
        sgnx = 0 if ox == tx else (1 if ox < tx else -1)
        sgny = 0 if oy == ty else (1 if oy < ty else -1)
        # Blocking cell roughly one step from opponent toward the target; if we approach it, we likely interfere.
        bx, by = ox + sgnx, oy + sgny
        block_dist = man(nme, (bx, by)) if inb(bx, by) else man(nme, opp_target)
        prev_block_dist = man(me, (bx, by)) if inb(bx, by) else man(me, opp_target)
        block_improve = prev_block_dist - block_dist

        # Also slightly prefer moving generally toward self_target to avoid stagnation.
        general = -(man(nme, self_target))

        val = (d0 - d1) + cap_bonus + k_block * block_improve + 0.03 * general
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move