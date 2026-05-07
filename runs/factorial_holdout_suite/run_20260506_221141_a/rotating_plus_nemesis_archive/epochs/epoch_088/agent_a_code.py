def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Strategy shift vs prior: avoid contesting near-opponent resources; prioritize resources that
    # are both closer to us than to them AND "row-aligned" advantage (opponent tends to sweep rows).
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index") or 0)

    best_move = [0, 0]
    best_val = -10**18

    # Choose target cell score; then choose move that maximizes best reachable target.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Row/anti-row bias: if opponent is on a row, prefer resources on rows with opposite parity.
        row_parity_bias = 1 if (ny % 2) != (oy % 2) else 0
        # Small deterministic oscillation to keep behavior from repeating on ties.
        osc = 0.001 * (((nx + ny + turn) % 7) - 3)

        if not resources:
            val = (man(nx, ny, ox, oy)) + 2 * row_parity_bias + osc
        else:
            val = -10**18
            for tx, ty in resources:
                self_d = man(nx, ny, tx, ty)
                opp_d = man(ox, oy, tx, ty)

                # Main: we want resources where we can arrive earlier.
                # Secondary: avoid resources where opponent is already closer.
                # Tertiary: favor row parity away from opponent.
                arrive_adv = (opp_d - self_d)

                # Opponent sweep rows heuristic: favor matching our move's row with target's row parity.
                row_match = 1 if (ty % 2) == (oy % 2) else 0
                # Penalize targets on opponent's row parity when possible (we'd get swept/contested).
                row_contest_pen = 1 if row_match else 0

                score = 10 * arrive_adv - 2 * self_d + 3 * row_parity_bias - 4 * row_contest_pen + osc
                if score > val:
                    val = score

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move