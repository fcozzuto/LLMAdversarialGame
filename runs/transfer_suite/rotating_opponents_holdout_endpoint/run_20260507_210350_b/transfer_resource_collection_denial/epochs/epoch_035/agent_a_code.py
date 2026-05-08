def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx = w - 1 if sx < w // 2 else 0
        ty = h - 1 if sy < h // 2 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    my_quad_bonus = 1 if sx < w // 2 else -1
    opp_quad_bonus = -my_quad_bonus

    best = None
    for dx, dy, nx, ny in cand:
        # Evaluate how strong our next-step position is versus all resources.
        # Prefer moving that creates a positive (or larger) lead.
        best_adv = -10**9
        best_tie = None
        for tx, ty in resources:
            myd = man(nx, ny, tx, ty)
            opd = man(ox, oy, tx, ty)
            adv = opd - myd  # positive means we arrive sooner
            # If opponent is already closer, slightly prefer resources closer to our side.
            side = (1 if tx < w // 2 else -1) * my_quad_bonus + (1 if ty < h // 2 else -1) * my_quad_bonus
            # Encourage picking resources near our current row/col alignment (good vs sweep patterns).
            align = -min(abs(ty - ny), abs(tx - nx))
            key = (-(adv + 0.25 * side), myd, abs(tx - nx) + abs(ty - ny), tx, ty)
            if best_tie is None or key < best_tie:
                best_tie = key
                best_adv = adv
        # Deterministic tie-break: also prefer smaller immediate distance to the chosen target.
        immediate = min(mnad for _, mndad in [(0, 0)] ) if False else 0
        # Add a small preference for not moving away when leads are small.
        move_cost = abs(dx) + abs(dy)
        final_key = (-best_adv, best_tie[1] + 0.1 * move_cost, dx, dy)
        if best is None or final_key < best[0]:
            best = (final_key, [dx, dy])

    return best[1]