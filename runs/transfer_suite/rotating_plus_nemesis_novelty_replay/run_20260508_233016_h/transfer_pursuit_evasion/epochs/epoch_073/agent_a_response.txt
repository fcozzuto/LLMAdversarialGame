def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "")
    # If we're an evader, maximize distance from opponent; else minimize.
    is_evader = "evader" in self_role.lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_moves = []
    best_val = None

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Evader: prefer hugging borders (reduces interception paths), but avoid too-close corners if blocked.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        if is_evader:
            # Larger distance better; add border preference.
            border = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
            # Smaller border means closer to edge; reward closeness deterministically.
            edge_bonus = (w - 1 + h - 1) - (2 * border)
            val = (d * 10.0) + (edge_bonus)
        else:
            # Pursuer: smaller distance better; also slightly prefer progressing toward center to avoid walls.
            border = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
            val = (-d * 10.0) + (border * 0.1)

        if best_val is None or val > best_val:
            best_val = val
            best_moves = [(dx, dy)]
        elif val == best_val:
            best_moves.append((dx, dy))

    # Deterministic tie-break: smallest dx then smallest dy.
    best_moves.sort()
    return [int(best_moves[0][0]), int(best_moves[0][1])]