def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def res_set():
        return set((r[0], r[1]) for r in resources)

    rset = res_set()
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Deterministic: drift towards center line opposing diagonal.
        dx = sign(ox - x) * -1
        dy = sign(oy - y) * -1
        nx, ny = x + dx, y + dy
        return [dx if inb(nx, y) else 0, dy if inb(x, ny) else 0]

    # Pick a best target resource deterministically (no search over full grid).
    best = None
    best_key = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_op = abs(tx - ox) + abs(ty - oy)
        key = ((d_op - d_me), -d_me, d_op, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Move scoring: maximize advantage while making progress; strong penalty for obstacles.
    def cell_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        d_me = abs(tx - nx) + abs(ty - ny)
        d_op = abs(tx - ox) + abs(ty - oy)
        # Bonus if we can land on any remaining resource; else prefer reducing distance to chosen target.
        on_any = 1 if (nx, ny) in rset else 0
        # Secondary term: avoid letting opponent be closer to the same target after our move.
        d_op_new = abs(tx - ox) + abs(ty - oy)
        # Use a small tie-break on moving towards target vs moving away.
        return (on_any * 2000) + ((d_op_new - d_me) * 120) - (d_me * 3) + ((tx - nx) * 0 + (ty - ny) * 0)

    # Try best move among legal deltas; deterministic tie-break by fixed move order and then parity.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            val = -10**8
        else:
            val = cell_score(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer moves that reduce distance to chosen target, then smaller (dx,dy).
            curd = abs((x + best_move[0]) - tx) + abs((y + best_move[1]) - ty)
            nd = abs(nx - tx) + abs(ny - ty)
            if nd < curd or (nd == curd and (dx, dy) < best_move):
                best_move = (dx, dy)

    dx, dy = best_move
    # Final safety: keep within bounds; if not, stay.
    if not inb(x + dx, y + dy):
        return [0, 0]
    return [int(dx), int(dy)]